data "aws_iam_role" "bookify_ec2" {
  name = "bookify-ec2-role"
}

resource "aws_iam_role_policy" "bookify_ec2_ecr" {
  name = "bookify-ec2-ecr-pull"
  role = data.aws_iam_role.bookify_ec2.name

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Sid    = "ECRAuthorization"
        Effect = "Allow"

        Action = [
          "ecr:GetAuthorizationToken"
        ]

        Resource = "*"
      },
      {
        Sid    = "ECRPull"
        Effect = "Allow"

        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]

        Resource = aws_ecr_repository.bookify.arn
      }
    ]
  })
}
