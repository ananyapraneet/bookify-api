data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_vpc" "bookify" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name        = "${var.project_name}-vpc"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_subnet" "bookify_public" {
  vpc_id                  = aws_vpc.bookify.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = {
    Name        = "${var.project_name}-public-subnet"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_internet_gateway" "bookify" {
  vpc_id = aws_vpc.bookify.id

  tags = {
    Name        = "${var.project_name}-igw"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_route_table" "bookify_public" {
  vpc_id = aws_vpc.bookify.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.bookify.id
  }

  tags = {
    Name        = "${var.project_name}-public-rt"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_route_table_association" "bookify_public" {
  subnet_id      = aws_subnet.bookify_public.id
  route_table_id = aws_route_table.bookify_public.id
}
