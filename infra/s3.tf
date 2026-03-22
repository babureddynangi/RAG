resource "aws_s3_bucket" "main" {
  bucket = "${var.project}-${data.aws_caller_identity.current.account_id}"
}
data "aws_caller_identity" "current" {}
resource "aws_s3_object" "chunks" {
  bucket = aws_s3_bucket.main.id
  key    = "data/chunks.json"
  source = "../app/data/chunks.json"
}
resource "aws_s3_object" "stages" {
  bucket = aws_s3_bucket.main.id
  key    = "data/stages.yaml"
  source = "../app/data/stages.yaml"
}
