clean:
	rm -rf package build

package:
	mkdir -p package build
	pip install --target ./package requests pyyaml
	cd package && zip -r ../build/lambda_package.zip .
	cd src && zip -r ../build/lambda_package.zip *.py
	cp build/lambda_package.zip build/lambda_package-2.zip
	zip -r build/lambda_package.zip config.yaml
