import * as cdk from 'aws-cdk-lib';
import {LambdaEventBridge} from "../lib/stack/lambda-event-bridge";

const app = new cdk.App();

new LambdaEventBridge(app, 'LambdaEventBridgeStack')