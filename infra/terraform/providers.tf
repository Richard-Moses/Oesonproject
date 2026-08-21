terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.14" # Match the version in your lock file
    }
  }
}

provider "aws" {
  region = "eu-west-2"
}