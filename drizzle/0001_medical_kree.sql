CREATE TABLE `agent_activity` (
	`id` int AUTO_INCREMENT NOT NULL,
	`clientId` int NOT NULL,
	`agentId` int NOT NULL,
	`agentName` varchar(255) NOT NULL,
	`status` enum('online','standby','offline') NOT NULL DEFAULT 'online',
	`lastActivityAt` timestamp,
	`totalInvocations` int DEFAULT 0,
	`successCount` int DEFAULT 0,
	`errorCount` int DEFAULT 0,
	`averageResponseTime` int DEFAULT 0,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `agent_activity_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `alerts` (
	`id` int AUTO_INCREMENT NOT NULL,
	`clientId` int NOT NULL,
	`transactionId` int,
	`cashierId` int,
	`ruleId` varchar(10) NOT NULL,
	`ruleName` varchar(255) NOT NULL,
	`severity` enum('LOW','MEDIUM','HIGH','CRITICAL') NOT NULL DEFAULT 'MEDIUM',
	`description` text,
	`amount` int,
	`confidence` decimal(5,2) DEFAULT '0.00',
	`status` enum('NEW','ACKNOWLEDGED','RESOLVED','FALSE_POSITIVE') NOT NULL DEFAULT 'NEW',
	`acknowledgedAt` timestamp,
	`resolvedAt` timestamp,
	`notes` text,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `alerts_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `audit_logs` (
	`id` int AUTO_INCREMENT NOT NULL,
	`userId` int,
	`clientId` int,
	`action` varchar(255) NOT NULL,
	`resource` varchar(255),
	`resourceId` int,
	`details` json,
	`ipAddress` varchar(45),
	`userAgent` text,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `audit_logs_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `cashiers` (
	`id` int AUTO_INCREMENT NOT NULL,
	`clientId` int NOT NULL,
	`name` varchar(255) NOT NULL,
	`email` varchar(320),
	`phone` varchar(20),
	`riskScore` decimal(5,2) DEFAULT '0.00',
	`riskLevel` enum('LOW','MEDIUM','HIGH') NOT NULL DEFAULT 'LOW',
	`voidCount` int DEFAULT 0,
	`voidRate` decimal(5,2) DEFAULT '0.00',
	`totalTransactions` int DEFAULT 0,
	`anomalyCount` int DEFAULT 0,
	`lastActivityAt` timestamp,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `cashiers_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `clients` (
	`id` int AUTO_INCREMENT NOT NULL,
	`clientId` varchar(64) NOT NULL,
	`name` varchar(255) NOT NULL,
	`businessName` varchar(255) NOT NULL,
	`email` varchar(320) NOT NULL,
	`phone` varchar(20) NOT NULL,
	`tier` enum('DEMO','V-LITE','V-PRO','V-ADVANCE','V-ELITE','V-ULTRA') NOT NULL DEFAULT 'DEMO',
	`status` enum('pending','aktif','suspended','cancelled') NOT NULL DEFAULT 'pending',
	`passwordHash` varchar(255) NOT NULL,
	`ktpUrl` text,
	`monthlyPrice` int DEFAULT 0,
	`setupFee` int DEFAULT 0,
	`commissionRate` decimal(5,2) DEFAULT '0.00',
	`referrerId` int,
	`demoStartTime` datetime,
	`demoEndTime` datetime,
	`activatedAt` timestamp,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `clients_id` PRIMARY KEY(`id`),
	CONSTRAINT `clients_clientId_unique` UNIQUE(`clientId`)
);
--> statement-breakpoint
CREATE TABLE `investor_returns` (
	`id` int AUTO_INCREMENT NOT NULL,
	`month` varchar(7) NOT NULL,
	`mrr` int DEFAULT 0,
	`totalRevenue` int DEFAULT 0,
	`expenses` int DEFAULT 0,
	`netProfit` int DEFAULT 0,
	`roiPercentage` decimal(8,2) DEFAULT '0.00',
	`yield` decimal(8,2) DEFAULT '0.00',
	`payoutAmount` int DEFAULT 0,
	`isPaid` boolean DEFAULT false,
	`paidAt` timestamp,
	`notes` text,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `investor_returns_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `invoices` (
	`id` int AUTO_INCREMENT NOT NULL,
	`clientId` int NOT NULL,
	`invoiceNumber` varchar(64) NOT NULL,
	`tier` enum('V-LITE','V-PRO','V-ADVANCE','V-ELITE','V-ULTRA') NOT NULL,
	`type` enum('MONTHLY','SETUP','UPGRADE') NOT NULL DEFAULT 'MONTHLY',
	`amount` int NOT NULL,
	`monthlyPrice` int DEFAULT 0,
	`setupFee` int DEFAULT 0,
	`status` enum('PENDING','PAID','OVERDUE','CANCELLED') NOT NULL DEFAULT 'PENDING',
	`paymentMethod` varchar(64),
	`paymentProof` text,
	`dueDate` datetime NOT NULL,
	`paidAt` timestamp,
	`notes` text,
	`whatsappLink` text,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `invoices_id` PRIMARY KEY(`id`),
	CONSTRAINT `invoices_invoiceNumber_unique` UNIQUE(`invoiceNumber`)
);
--> statement-breakpoint
CREATE TABLE `referrals` (
	`id` int AUTO_INCREMENT NOT NULL,
	`referrerId` int NOT NULL,
	`referredClientId` int NOT NULL,
	`referralLink` varchar(255) NOT NULL,
	`status` enum('PENDING','ACTIVE','INACTIVE') NOT NULL DEFAULT 'PENDING',
	`commissionRate` decimal(5,2) DEFAULT '10.00',
	`commissionAmount` int DEFAULT 0,
	`isPaid` boolean DEFAULT false,
	`paidAt` timestamp,
	`clickCount` int DEFAULT 0,
	`conversionDate` timestamp,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `referrals_id` PRIMARY KEY(`id`),
	CONSTRAINT `referrals_referralLink_unique` UNIQUE(`referralLink`)
);
--> statement-breakpoint
CREATE TABLE `sessions` (
	`id` int AUTO_INCREMENT NOT NULL,
	`clientId` int NOT NULL,
	`token` varchar(255) NOT NULL,
	`ipAddress` varchar(45),
	`userAgent` text,
	`expiresAt` timestamp NOT NULL,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `sessions_id` PRIMARY KEY(`id`),
	CONSTRAINT `sessions_token_unique` UNIQUE(`token`)
);
--> statement-breakpoint
CREATE TABLE `transactions` (
	`id` int AUTO_INCREMENT NOT NULL,
	`clientId` int NOT NULL,
	`cashierId` int,
	`transactionId` varchar(64) NOT NULL,
	`branch` varchar(255),
	`cashierName` varchar(255),
	`amount` int NOT NULL,
	`type` enum('PENJUALAN','VOID','DISKON','REFUND') NOT NULL,
	`status` enum('NORMAL','ANOMALI') NOT NULL DEFAULT 'NORMAL',
	`physicalBalance` int,
	`systemBalance` int,
	`balanceDifference` int,
	`fraudFlags` json DEFAULT ('[]'),
	`fraudConfidence` decimal(5,2) DEFAULT '0.00',
	`timestamp` datetime NOT NULL,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `transactions_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
ALTER TABLE `agent_activity` ADD CONSTRAINT `agent_activity_clientId_clients_id_fk` FOREIGN KEY (`clientId`) REFERENCES `clients`(`id`) ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE `alerts` ADD CONSTRAINT `alerts_clientId_clients_id_fk` FOREIGN KEY (`clientId`) REFERENCES `clients`(`id`) ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE `alerts` ADD CONSTRAINT `alerts_transactionId_transactions_id_fk` FOREIGN KEY (`transactionId`) REFERENCES `transactions`(`id`) ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE `alerts` ADD CONSTRAINT `alerts_cashierId_cashiers_id_fk` FOREIGN KEY (`cashierId`) REFERENCES `cashiers`(`id`) ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE `audit_logs` ADD CONSTRAINT `audit_logs_userId_users_id_fk` FOREIGN KEY (`userId`) REFERENCES `users`(`id`) ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE `audit_logs` ADD CONSTRAINT `audit_logs_clientId_clients_id_fk` FOREIGN KEY (`clientId`) REFERENCES `clients`(`id`) ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE `cashiers` ADD CONSTRAINT `cashiers_clientId_clients_id_fk` FOREIGN KEY (`clientId`) REFERENCES `clients`(`id`) ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE `clients` ADD CONSTRAINT `clients_referrerId_clients_id_fk` FOREIGN KEY (`referrerId`) REFERENCES `clients`(`id`) ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE `invoices` ADD CONSTRAINT `invoices_clientId_clients_id_fk` FOREIGN KEY (`clientId`) REFERENCES `clients`(`id`) ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE `referrals` ADD CONSTRAINT `referrals_referrerId_clients_id_fk` FOREIGN KEY (`referrerId`) REFERENCES `clients`(`id`) ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE `referrals` ADD CONSTRAINT `referrals_referredClientId_clients_id_fk` FOREIGN KEY (`referredClientId`) REFERENCES `clients`(`id`) ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE `sessions` ADD CONSTRAINT `sessions_clientId_clients_id_fk` FOREIGN KEY (`clientId`) REFERENCES `clients`(`id`) ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE `transactions` ADD CONSTRAINT `transactions_clientId_clients_id_fk` FOREIGN KEY (`clientId`) REFERENCES `clients`(`id`) ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE `transactions` ADD CONSTRAINT `transactions_cashierId_cashiers_id_fk` FOREIGN KEY (`cashierId`) REFERENCES `cashiers`(`id`) ON DELETE no action ON UPDATE no action;--> statement-breakpoint
CREATE INDEX `clientId_idx` ON `agent_activity` (`clientId`);--> statement-breakpoint
CREATE INDEX `agentId_idx` ON `agent_activity` (`agentId`);--> statement-breakpoint
CREATE INDEX `status_idx` ON `agent_activity` (`status`);--> statement-breakpoint
CREATE INDEX `clientId_idx` ON `alerts` (`clientId`);--> statement-breakpoint
CREATE INDEX `ruleId_idx` ON `alerts` (`ruleId`);--> statement-breakpoint
CREATE INDEX `status_idx` ON `alerts` (`status`);--> statement-breakpoint
CREATE INDEX `createdAt_idx` ON `alerts` (`createdAt`);--> statement-breakpoint
CREATE INDEX `userId_idx` ON `audit_logs` (`userId`);--> statement-breakpoint
CREATE INDEX `clientId_idx` ON `audit_logs` (`clientId`);--> statement-breakpoint
CREATE INDEX `action_idx` ON `audit_logs` (`action`);--> statement-breakpoint
CREATE INDEX `createdAt_idx` ON `audit_logs` (`createdAt`);--> statement-breakpoint
CREATE INDEX `clientId_idx` ON `cashiers` (`clientId`);--> statement-breakpoint
CREATE INDEX `riskLevel_idx` ON `cashiers` (`riskLevel`);--> statement-breakpoint
CREATE INDEX `clientId_idx` ON `clients` (`clientId`);--> statement-breakpoint
CREATE INDEX `tier_idx` ON `clients` (`tier`);--> statement-breakpoint
CREATE INDEX `status_idx` ON `clients` (`status`);--> statement-breakpoint
CREATE INDEX `month_idx` ON `investor_returns` (`month`);--> statement-breakpoint
CREATE INDEX `isPaid_idx` ON `investor_returns` (`isPaid`);--> statement-breakpoint
CREATE INDEX `clientId_idx` ON `invoices` (`clientId`);--> statement-breakpoint
CREATE INDEX `invoiceNumber_idx` ON `invoices` (`invoiceNumber`);--> statement-breakpoint
CREATE INDEX `status_idx` ON `invoices` (`status`);--> statement-breakpoint
CREATE INDEX `dueDate_idx` ON `invoices` (`dueDate`);--> statement-breakpoint
CREATE INDEX `referrerId_idx` ON `referrals` (`referrerId`);--> statement-breakpoint
CREATE INDEX `referredClientId_idx` ON `referrals` (`referredClientId`);--> statement-breakpoint
CREATE INDEX `status_idx` ON `referrals` (`status`);--> statement-breakpoint
CREATE INDEX `clientId_idx` ON `sessions` (`clientId`);--> statement-breakpoint
CREATE INDEX `token_idx` ON `sessions` (`token`);--> statement-breakpoint
CREATE INDEX `expiresAt_idx` ON `sessions` (`expiresAt`);--> statement-breakpoint
CREATE INDEX `clientId_idx` ON `transactions` (`clientId`);--> statement-breakpoint
CREATE INDEX `cashierId_idx` ON `transactions` (`cashierId`);--> statement-breakpoint
CREATE INDEX `status_idx` ON `transactions` (`status`);--> statement-breakpoint
CREATE INDEX `timestamp_idx` ON `transactions` (`timestamp`);