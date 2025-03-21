terraform {
  # Note, this is a partial Terraform backend configuration. The missing arguments are passed at runtime
  # https://www.terraform.io/docs/language/settings/backends/configuration.html#partial-configuration
  backend "s3" {
    encrypt = "true"
  }
}

data "terraform_remote_state" "kubernetes" {
  backend = "s3"
  config  = {
    bucket = local.EKS_BUCKET
    key    = local.EKS_S3_KEY
    region = var.AWS_REGION
  }
}