variable "queue_name" {
  type = string
}

variable "is_fifo" {
  type    = bool
  default = false
}

variable "environment" {
  type = string
}