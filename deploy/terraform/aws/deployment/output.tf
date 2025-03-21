output GUID {
  value = random_string.guid.result
}

output NAMESPACE {
  value = "${lower(var.NAMESPACE)}-${random_string.guid.result}"
}

output ECR_REPO_NAME {
  value = var.ECR_REPO_NAME
}