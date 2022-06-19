terraform {
  backend "remote" {
    hostname = "app.terraform.io"
    organization = "ruse"

    workspaces {
      name = "aws-jita"
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