provider "aws" {
  region = "ap-southeast-2"

  default_tags {
    tags = {
      "ctm:environment"     = var.ENVIRONMENT_SHORT
      "ctm:vertical"        = var.VERTICAL
      "ctm:role"            = "deployment"
      "ctm:confidentiality" = "restricted"
      "ctm:contains-pii"    = "++NOTSET++"
      "ctm:terraform"       = var.ECR_REPO_NAME
    }
  }
}

provider "argocd" {
  server_addr = var.ARGOCD_DOMAIN
  username    = local.username
  password    = local.password
  grpc_web    = true
  headers     = [
    "CF-Access-Client-Id: ${var.CF_ACCESS_ID}",
    "CF-Access-Client-Secret: ${var.CF_ACCESS_SECRET}"
  ]
}
