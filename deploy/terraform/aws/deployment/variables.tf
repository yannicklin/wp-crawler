variable "AWS_REGION" {
  type        = string
  description = "AWS region"
  default     = "ap-southeast-2"
}
variable "ENVIRONMENT" {
  type        = string
  description = "Staging environment name"
}
variable "ENVIRONMENT_SHORT" {
  type        = string
  description = "Short environment name"
}
variable "NAMESPACE" {
  type        = string
  description = "Namespace for the K8s deployment"
}
variable "FEATURE" {
  type        = string
  description = "Name of the feature if applicable"
  default     = ""
}
variable "ECR_REPO_NAME" {
  type        = string
  description = "Image for the ECR Repository"
}
variable "ECR_VERSION" {
  type        = string
  description = "Image for the ECR Repository"
}
variable "HELM_VERSION" {
  type        = string
  description = "Image for the ECR Repository"
}
variable "TF_MODULE_VERSION" {
  type        = string
  description = "Version for the Terraform Module"
}
variable "VERTICAL" {
  type        = string
  description = "Vertical we are building for"
}
variable "ARGOCD_CREDS" {
  description = "Argocd credentials as json"
  sensitive   = true
}
variable "ARGOCD_DOMAIN" {
  type        = string
  description = "Argocd endpoint"
}
variable "CF_ACCESS_ID" {
  description = "Access ID for service token"
  type        = string
  sensitive   = true
}
variable "CF_ACCESS_SECRET" {
  description = "Access Secret for service token"
  type        = string
  sensitive   = true
}
variable "GIT_HASH" {
  description = "The commit for the repo building the project"
  type        = string
}
variable "CONTAINER_PORT" {
  description = "The port the service should be running on"
  type        = string
  default     = 1337
}