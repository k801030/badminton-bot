import * as cdk from 'aws-cdk-lib';
import {Duration, TimeZone} from 'aws-cdk-lib';
import {Construct} from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as scheduler from 'aws-cdk-lib/aws-scheduler';
import * as targets from 'aws-cdk-lib/aws-scheduler-targets';
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

        // Grant Lambda permission to read from SSM Parameter Store
        lambdaRole.addToPolicy(new PolicyStatement({
            actions: ['ssm:GetParameter'],
            resources: ['*'],
        }));

        // Lambda Function
        const handler = new lambda.Function(this, 'LambdaHandler', {
            functionName: 'BadmintonBot',
            runtime: lambda.Runtime.PYTHON_3_14,
            handler: 'lambda_function.handler',
            code: lambda.Code.fromAsset(path.join(__dirname, '../../../app')),
            role: lambdaRole,
            timeout: Duration.minutes(15),
        });

        // Create EventBridge Scheduler schedules for each weekday and account event
        for (const [weekday, enabled] of WeekdayEventRules) {
            const schedule = this.scheduleByWeekday(weekday);
            for (const event of Events) {
                new scheduler.Schedule(this, `EventSchedule-${weekday}-Account${event.accountId}`, {
                    scheduleName: `badminton-reservation-${weekday.toLowerCase()}-account-${event.accountId}`,
                    description: `execute at 10pm UK timezone (account ${event.accountId})`,
                    schedule: schedule,
                    enabled: enabled,
                    target: new targets.LambdaInvoke(handler, {
                        input: scheduler.ScheduleTargetInput.fromObject(event),
                    }),
                });
            }
        }
    }

    // Helper method to generate cron schedules for EventBridge Scheduler based on weekday
    private scheduleByWeekday(weekday: string): scheduler.ScheduleExpression {
        return scheduler.ScheduleExpression.cron({
            minute: "59",
            hour: "21", // 21:59 UK time (automatically adjusts for BST/GMT)
            month: "*",
            weekDay: weekday,
            year: "*",
            timeZone: TimeZone.EUROPE_LONDON,
        })
    }
}
