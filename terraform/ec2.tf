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
  ami           = data.aws_ssm_parameter.amazon_linux_2023_arm64.value
  instance_type = "t4g.small"

  subnet_id                   = aws_subnet.bookify_public.id
  vpc_security_group_ids      = [aws_security_group.bookify_ec2.id]
  associate_public_ip_address = true

  key_name = aws_key_pair.bookify.key_name

  iam_instance_profile = "bookify-ec2-role"

  user_data = <<-EOF
    #!/bin/bash
    set -eux

    dnf update -y

    dnf install -y docker git

    systemctl enable docker
    systemctl start docker

    usermod -aG docker ec2-user
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
