clean:
	rm -rf package build

package:
	mkdir -p package build
	pip install --target ./package requests pyyaml
	cd package && zip -r ../build/lambda_package.zip .
	cd ../
	cd src && zip -r ../build/lambda_package.zip *.py
	cd ../
	zip -r build/lambda_package.zip config.yaml
