variable "aws_region" {
  description = "AWS region where Bookify infrastructure will be deployed"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name used for AWS resource naming"
  type        = string
  default     = "bookify"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "production"
}

variable "admin_ip" {
  description = "Administrator public IP allowed to SSH into the EC2 instance"
  type        = string
}
