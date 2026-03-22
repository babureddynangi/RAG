output "api_url" { value = aws_apigatewayv2_api.main.api_endpoint }
output "dynamodb_table" { value = aws_dynamodb_table.chunks.name }
output "s3_bucket" { value = aws_s3_bucket.main.id }
