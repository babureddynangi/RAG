resource "aws_dynamodb_table" "chunks" {
  name         = "${var.project}-chunks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "chunk_id"
  attribute { name = "chunk_id" type = "S" }
  attribute { name = "primary_stage" type = "S" }
  global_secondary_index {
    name            = "primary_stage-index"
    hash_key        = "primary_stage"
    projection_type = "ALL"
  }
}
