import * as cdk from 'aws-cdk-lib';
import {Duration} from 'aws-cdk-lib';
import {Construct} from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import * as path from 'path';
import {ManagedPolicy, PolicyStatement, Role, ServicePrincipal} from "aws-cdk-lib/aws-iam";
import { WeekdayEventRules } from '../config/weekday-event-rules';
import { Events } from '../data/events';

export class LambdaEventBridge extends cdk.Stack {
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        // Lambda Role
        const lambdaRole = new Role(this, 'LambdaBasicRole', {
            roleName: 'LambdaRole',
            assumedBy: new ServicePrincipal('lambda.amazonaws.com'),
        });

        lambdaRole.addManagedPolicy(ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole'));

        // Grant Lambda permission to read from Secrets Manager
        lambdaRole.addToPolicy(new PolicyStatement({
            actions: ['secretsmanager:GetSecretValue'],
            resources: ['*'],
        }));

        // Lambda Function
        const handler = new lambda.Function(this, 'LambdaHandler', {
            functionName: 'BadmintonBot',
            runtime: lambda.Runtime.PYTHON_3_10,
            handler: 'lambda_function.handler',
            code: lambda.Code.fromAsset(path.join(__dirname, '../../../app')),
            role: lambdaRole,
            timeout: Duration.minutes(15),
        });

        // Create EventBridge rules for each weekday defined in WeekdayEventRules
        const rules = []
        for (const [weekday, enabled] of WeekdayEventRules) {
            rules.push(
                new events.Rule(this, `EventRule-${weekday}`, {
                    ruleName: `badminton-reservation-${weekday.toLowerCase()}`,
                    description: `execute at 10pm UK timezone`,
                    schedule: this.scheduleByWeekday(weekday),
                    enabled: enabled,
                })
            )
        }

        // Attach the Lambda function as a target to each EventBridge rule
        // Pass the event data as the input payload to the Lambda function
        for (const event of Events) {
            for (const rule of rules) {
                rule.addTarget(new targets.LambdaFunction(handler, {
                    event: events.RuleTargetInput.fromObject(event)
                }));
            }
        }
    }

    // Helper method to generate cron schedules for EventBridge rules based on weekday
    private scheduleByWeekday(weekday: string): events.Schedule {
        return events.Schedule.cron({
            minute: "59",
            hour: "20,21", // 20:59 and 21:59 UK time
            month: "*",
            weekDay: weekday,
            year: "*",
        })
    }
}
