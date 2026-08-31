resource "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"

  client_id_list = [
    "sts.amazonaws.com"
  ]

  tags = {
    Name        = "${var.project_name}-github-oidc"
    Environment = var.environment
    Project     = var.project_name
  }
}

data "aws_iam_policy_document" "github_actions_assume_role" {
  statement {
    effect = "Allow"

    actions = [
      "sts:AssumeRoleWithWebIdentity"
    ]

    principals {
      type = "Federated"

      identifiers = [
        aws_iam_openid_connect_provider.github.arn
      ]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"

      values = [
        "sts.amazonaws.com"
      ]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:sub"

      values = [
        "repo:ananyapraneet/bookify-api:ref:refs/heads/main"
      ]
    }
  }
}

resource "aws_iam_role" "github_actions" {
  name = "${var.project_name}-github-actions"

  assume_role_policy = data.aws_iam_policy_document.github_actions_assume_role.json

  tags = {
    Name        = "${var.project_name}-github-actions"
    Environment = var.environment
    Project     = var.project_name
  }
}

data "aws_iam_policy_document" "github_actions_ecr" {
  statement {
    effect = "Allow"

    actions = [
      "ecr:GetAuthorizationToken"
    ]

    resources = [
      "*"
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:CompleteLayerUpload",
      "ecr:InitiateLayerUpload",
      "ecr:PutImage",
      "ecr:UploadLayerPart"
    ]

    resources = [
      aws_ecr_repository.bookify.arn
    ]
  }
}

resource "aws_iam_role_policy" "github_actions_ecr" {
  name = "${var.project_name}-github-actions-ecr"
  role = aws_iam_role.github_actions.id

  policy = data.aws_iam_policy_document.github_actions_ecr.json
}

data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "github_actions_ssm" {
  statement {
    effect = "Allow"

    actions = [
      "ssm:SendCommand"
    ]

    resources = [
      "arn:aws:ssm:${var.aws_region}:*:document/AWS-RunShellScript",
      aws_instance.bookify.arn
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "ssm:GetCommandInvocation"
    ]

    resources = [
      "*"
    ]
  }
}

resource "aws_iam_role_policy" "github_actions_ssm" {
  name   = "${var.project_name}-github-actions-ssm"
  role   = aws_iam_role.github_actions.id
  policy = data.aws_iam_policy_document.github_actions_ssm.json
}
