clean:
	rm -rf package build

package:
	mkdir -p package build
	pip install --target ./package requests pyyaml
	cd package && zip -r ../build/lambda_package.zip .
	cd src && zip -r ../build/lambda_package.zip *.py
	zip -r build/lambda_package.zip config.yaml
