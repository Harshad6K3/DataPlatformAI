variable "vpc_cidr" {
  type = string
}

variable "environment" {
  type = string
}

variable "az_count" {
  type    = number
  default = 2
}

variable "enable_nat_gateway" {
  type    = bool
  default = true
}