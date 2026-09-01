data "aws_ssm_parameter" "amazon_linux_2023_arm64" {
  name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-arm64"
}

resource "aws_key_pair" "bookify" {
  key_name   = "${var.project_name}-ec2-key"
  public_key = file(pathexpand("~/.ssh/id_rsa.pub"))

  tags = {
    Name        = "${var.project_name}-ec2-key"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_instance" "bookify" {
  ami           = "ami-0cded71ff6ab7f608"
  instance_type = "t4g.small"

  subnet_id                   = aws_subnet.bookify_public.id
  vpc_security_group_ids      = [aws_security_group.bookify_ec2.id]
  associate_public_ip_address = true

  key_name = aws_key_pair.bookify.key_name

  iam_instance_profile = "bookify-ec2-role"

  user_data_replace_on_change = false

  lifecycle {
    create_before_destroy = true

    ignore_changes = [
      ami
    ]
  }

  user_data = <<-EOF
      #!/bin/bash
      set -eux

      dnf update -y

      # Core packages
      dnf install -y docker git curl unzip

      # AWS CLI v2
      curl "https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip" -o "/tmp/awscliv2.zip"
      unzip -q /tmp/awscliv2.zip -d /tmp
      /tmp/aws/install
      rm -rf /tmp/aws /tmp/awscliv2.zip

      # Docker
      systemctl enable docker
      systemctl start docker
      usermod -aG docker ec2-user

      # Docker Compose plugin
      mkdir -p /usr/libexec/docker/cli-plugins

      curl -SL \
  	https://github.com/docker/compose/releases/latest/download/docker-compose-linux-aarch64 \
  	-o /usr/libexec/docker/cli-plugins/docker-compose

      chmod +x /usr/libexec/docker/cli-plugins/docker-compose

      # Verify Docker Compose
      docker compose version

      # Application directory
      mkdir -p /opt/bookify
      chown -R ec2-user:ec2-user /opt/bookify

      # Clone application repository
      if [ ! -d /opt/bookify/.git ]; then
        sudo -u ec2-user git clone \
          https://github.com/ananyapraneet/bookify-api.git \
          /opt/bookify
      fi

      chown -R ec2-user:ec2-user /opt/bookify

      # Make deployment script executable
      if [ -f /opt/bookify/scripts/deploy.sh ]; then
        chmod +x /opt/bookify/scripts/deploy.sh
      fi
    EOF

  root_block_device {
    volume_type           = "gp3"
    volume_size           = 20
    encrypted             = true
    delete_on_termination = true
  }

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
  }

  tags = {
    Name        = "${var.project_name}-ec2"
    Environment = var.environment
    Project     = var.project_name
  }
}
