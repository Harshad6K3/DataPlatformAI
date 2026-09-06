locals {
  suffix = var.is_fifo ? ".fifo" : ""
}

resource "aws_sqs_queue" "dlq" {
  name                        = "${var.queue_name}-dlq${local.suffix}"
  fifo_queue                  = var.is_fifo
  content_based_deduplication = var.is_fifo
  tags                        = { Environment = var.environment }
}

resource "aws_sqs_queue" "this" {
  name                        = "${var.queue_name}${local.suffix}"
  fifo_queue                  = var.is_fifo
  content_based_deduplication = var.is_fifo
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = 3
  })
  tags = { Environment = var.environment }
}