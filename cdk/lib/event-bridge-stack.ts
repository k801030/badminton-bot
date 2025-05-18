import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import * as path from 'path';

export class EventBridgeStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Lambda Function
    const eventHandler = new lambda.Function(this, 'EventHandler', {
      runtime: lambda.Runtime.NODEJS_18_X,
      handler: 'handler.handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../lambda')),
    });

    // EventBridge Rule (runs every 5 minutes)
    const rule = new events.Rule(this, 'EveryFiveMinutes', {
      schedule: events.Schedule.rate(cdk.Duration.minutes(5)),
    });

    // Add Lambda as target
    rule.addTarget(new targets.LambdaFunction(eventHandler));
  }
}
