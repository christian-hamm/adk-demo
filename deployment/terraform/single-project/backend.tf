terraform {
  backend "gcs" {
    bucket = "adk-demo-prod-499613-terraform-state"
    prefix = "adk-demo/dev"
  }
}
