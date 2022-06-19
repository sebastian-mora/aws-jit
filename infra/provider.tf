terraform {
  backend "remote" {
    hostname = "app.terraform.io"
    organization = "ruse"

    workspaces {
      name = "aws-jit"
    }
  }
}

provider "aws" {
  region = var.region
  default_tags {
    tags = {
      "system" = "jita"
    }
  }
}