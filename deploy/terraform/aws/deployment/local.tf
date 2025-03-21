locals {
  EKS_BUCKET     = "ctm-tf-state-${var.ENVIRONMENT}"
  EKS_S3_KEY     = "ctm/${var.ENVIRONMENT}/eks-cluster/eks-cluster.${var.ENVIRONMENT_SHORT}.${var.ENVIRONMENT}-new.tfstate"
  username       = jsondecode(var.ARGOCD_CREDS)["username"]
  password       = jsondecode(var.ARGOCD_CREDS)["password"]
  namespace_uniq = var.FEATURE != "" ? random_string.guid.result : "main"
}