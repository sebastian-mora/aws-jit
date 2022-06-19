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
  default_tags {
    tags = {
      "system" = "jita"
    }
  }
}