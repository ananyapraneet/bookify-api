output "ecr_repository_url" {
  description = "ECR repository URL"
  value       = aws_ecr_repository.bookify.repository_url
}

output "github_actions_role_arn" {
  description = "IAM role ARN assumed by GitHub Actions"
  value       = aws_iam_role.github_actions.arn
}
