import * as cdk from 'aws-cdk-lib';
import {Duration} from 'aws-cdk-lib';
import {Construct} from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import * as path from 'path';
import {EVENTS} from "./events";
import {ManagedPolicy, PolicyStatement, Role, ServicePrincipal} from "aws-cdk-lib/aws-iam";

export class LambdaEventBridge extends cdk.Stack {
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        // Lambda Role
        const lambdaRole = new Role(this, 'LambdaBasicRole', {
            roleName: 'LambdaRole',
            assumedBy: new ServicePrincipal('lambda.amazonaws.com'),
        });

        lambdaRole.addManagedPolicy(ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole'));

        // Add Secrets Manager read permission
        lambdaRole.addToPolicy(new PolicyStatement({
            actions: ['secretsmanager:GetSecretValue'],
            resources: ['*'],
        }));

        // Lambda Function
        const handler = new lambda.Function(this, 'LambdaHandler', {
            functionName: 'BadmintonBot',
            runtime: lambda.Runtime.PYTHON_3_10,
            handler: 'lambda_function.handler',
            code: lambda.Code.fromAsset(path.join(__dirname, '../../src')),
            role: lambdaRole,
            timeout: Duration.minutes(15),
        });

        // EventBridge Rule
        const rule = new events.Rule(this, 'EventRule', {
            ruleName: "badminton scheduled reservation",
            description: "10pm every Fri or Sat",
            schedule: events.Schedule.cron({
                minute: "59",
                hour: "20,21",
                month: "*",
                weekDay: "FRI",
                year: "*",
            }),
        });


        // Load JSON
        for (const event of EVENTS) {
            // Add Lambda as target
            rule.addTarget(new targets.LambdaFunction(handler, {
                event: events.RuleTargetInput.fromObject(event)
            }));
        }
    }
}
