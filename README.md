# Badminton Bot

## Deploy to AWS Lambda

```bash
mkdir -p package build
pip install --target ./package requests pyyaml
cd package
zip -r ../build/lambda_package.zip .
cd ../src
zip -r ../build/lambda_package.zip *.py
cd ..
```

## Cron
