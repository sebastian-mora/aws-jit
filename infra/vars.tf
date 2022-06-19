variable "jita_admin_policy_arn" {
  default = ""
}

variable "jita_request_timout" {
  type = number
  default = 3600 #seconds
}

variable "region" {
  type = string
  default = "us-west-2"
}