/**
 * MCP Tool Types - Generated from JSON Schema
 *
 * This file contains TypeScript interfaces generated from the MCP tools schema.
 * These types ensure type safety for tool inputs and outputs.
 */

// JSON Schema type definition
export interface JSONSchema7 {
  $id?: string;
  $schema?: string;
  $ref?: string;
  $comment?: string;
  title?: string;
  description?: string;
  default?: any;
  readOnly?: boolean;
  writeOnly?: boolean;
  examples?: any[];
  multipleOf?: number;
  maximum?: number;
  exclusiveMaximum?: number;
  minimum?: number;
  exclusiveMinimum?: number;
  maxLength?: number;
  minLength?: number;
  pattern?: string;
  additionalItems?: JSONSchema7;
  items?: JSONSchema7 | JSONSchema7[];
  maxItems?: number;
  minItems?: number;
  uniqueItems?: boolean;
  contains?: JSONSchema7;
  maxProperties?: number;
  minProperties?: number;
  required?: string[];
  additionalProperties?: JSONSchema7;
  definitions?: { [key: string]: JSONSchema7 };
  properties?: { [key: string]: JSONSchema7 };
  patternProperties?: { [key: string]: JSONSchema7 };
  dependencies?: { [key: string]: JSONSchema7 | string[] };
  propertyNames?: JSONSchema7;
  const?: any;
  enum?: any[];
  type?: string | string[];
  format?: string;
  contentMediaType?: string;
  contentEncoding?: string;
  if?: JSONSchema7;
  then?: JSONSchema7;
  else?: JSONSchema7;
  allOf?: JSONSchema7[];
  anyOf?: JSONSchema7[];
  oneOf?: JSONSchema7[];
  not?: JSONSchema7;
}

// Base types from schema definitions
export interface FilePath {
  type: 'string';
  minLength: 1;
  description: 'Absolute or repo-relative path';
}

export interface ProjectRoot {
  type: 'string';
  minLength: 1;
}

export interface RepoRoot {
  type: 'string';
  minLength: 1;
}

export interface Uri {
  type: 'string';
  format: 'uri';
}

export interface Globs {
  type: 'array';
  items: { type: 'string' };
}

export interface PathsOrGlobs {
  oneOf: [
    { type: 'array'; items: FilePath },
    Globs
  ];
}

export interface Range {
  type: 'object';
  required: ['startLine', 'startCol', 'endLine', 'endCol'];
  properties: {
    startLine: { type: 'integer'; minimum: 1 };
    startCol: { type: 'integer'; minimum: 1 };
    endLine: { type: 'integer'; minimum: 1 };
    endCol: { type: 'integer'; minimum: 1 };
  };
}

export interface Patch {
  type: 'string';
  description: 'Unified diff (git-compatible). Must include file headers and hunks.';
  minLength: 1;
}

export interface Patches {
  type: 'array';
  items: Patch;
}

export interface Diagnostic {
  type: 'object';
  required: ['ruleId', 'severity', 'location', 'message'];
  properties: {
    ruleId: { type: 'string' };
    severity: { type: 'string'; enum: ['info', 'warning', 'error'] };
    location: {
      type: 'object';
      required: ['filePath', 'line'];
      properties: {
        filePath: FilePath;
        line: { type: 'integer'; minimum: 1 };
        col: { type: 'integer'; minimum: 1 };
      };
    };
    message: { type: 'string' };
    quickFixId: { type: 'string' };
  };
}

export interface File {
  type: 'object';
  required: ['path', 'content'];
  properties: {
    path: FilePath;
    content: { type: 'string' };
    mode: { type: 'integer'; description: 'POSIX file mode (optional)' };
  };
}

export interface Files {
  type: 'array';
  items: File;
}

export interface Conflict {
  type: 'object';
  required: ['filePath', 'hunks'];
  properties: {
    filePath: FilePath;
    hunks: { type: 'array'; items: { type: 'string' } };
  };
}

export interface Endpoint {
  type: 'object';
  required: ['name', 'path', 'method'];
  properties: {
    name: { type: 'string' };
    path: { type: 'string' };
    method: { type: 'string'; enum: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'] };
  };
}

export interface GradleUpdates {
  type: 'array';
  items: {
    type: 'object';
    required: ['file', 'patch'];
    properties: {
      file: FilePath;
      patch: Patch;
    };
  };
}

export interface DataRef {
  type: 'object';
  required: ['type', 'value'];
  properties: {
    type: { type: 'string'; enum: ['path', 'inline', 'uri'] };
    value: { type: 'string' };
  };
}

export interface AuditId {
  type: 'string';
}

export interface SubjectId {
  type: 'string';
}

export interface AuditFilters {
  type: 'object';
  properties: {
    subjectId: SubjectId;
    op: { type: 'string' };
    dateRange: {
      type: 'object';
      required: ['from', 'to'];
      properties: {
        from: { type: 'string'; format: 'date-time' };
        to: { type: 'string'; format: 'date-time' };
      };
    };
    complianceTags: { type: 'array'; items: { type: 'string' } };
  };
}

export interface AuditEvent {
  type: 'object';
  required: ['id', 'timestamp', 'operation', 'subjectId'];
  properties: {
    id: AuditId;
    timestamp: { type: 'string'; format: 'date-time' };
    operation: { type: 'string' };
    subjectId: SubjectId;
    details: { type: 'object'; additionalProperties: true };
    complianceTags: { type: 'array'; items: { type: 'string' } };
  };
}

export interface BackupManifest {
  type: 'object';
  required: ['id', 'createdAt', 'entries'];
  properties: {
    id: { type: 'string' };
    createdAt: { type: 'string'; format: 'date-time' };
    entries: {
      type: 'array';
      items: {
        type: 'object';
        required: ['path', 'hash', 'size'];
        properties: {
          path: FilePath;
          hash: { type: 'string' };
          size: { type: 'integer'; minimum: 0 };
        };
      };
    };
  };
}

export interface ClassificationFinding {
  type: 'object';
  required: ['filePath', 'policy', 'line', 'snippet', 'confidence'];
  properties: {
    filePath: FilePath;
    policy: { type: 'string'; enum: ['PII', 'PHI', 'Secrets'] };
    line: { type: 'integer'; minimum: 1 };
    snippet: { type: 'string' };
    confidence: { type: 'number'; minimum: 0; maximum: 1 };
  };
}

export interface GitChange {
  type: 'object';
  required: ['path', 'status'];
  properties: {
    path: FilePath;
    status: { type: 'string'; enum: ['A', 'M', 'D', 'R', 'C', 'U'] };
  };
}

export interface AheadBehind {
  type: 'object';
  required: ['ahead', 'behind'];
  properties: {
    ahead: { type: 'integer'; minimum: 0 };
    behind: { type: 'integer'; minimum: 0 };
  };
}

export interface ApiSpec {
  type: 'object';
  required: ['baseUrl', 'path', 'method'];
  properties: {
    baseUrl: { type: 'string'; format: 'uri' };
    path: { type: 'string' };
    method: { type: 'string'; enum: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'] };
    headers: { type: 'object'; additionalProperties: { type: 'string' } };
    auth: {
      type: 'object';
      properties: {
        type: { type: 'string'; enum: ['None', 'ApiKey', 'OAuth2', 'JWT', 'Basic'] };
        tokenRef: DataRef;
      };
      additionalProperties: true;
    };
    query: { type: 'object'; additionalProperties: true };
  };
}

export interface MetricPoint {
  type: 'object';
  required: ['ts', 'name', 'value'];
  properties: {
    ts: { type: 'string'; format: 'date-time' };
    name: { type: 'string' };
    value: { type: 'number' };
    dimensions: { type: 'object'; additionalProperties: { type: 'string' } };
  };
}

export interface ComplianceViolation {
  type: 'object';
  required: ['policy', 'field', 'issue', 'severity'];
  properties: {
    policy: { type: 'string'; enum: ['GDPR', 'HIPAA'] };
    field: { type: 'string' };
    issue: { type: 'string' };
    severity: { type: 'string'; enum: ['low', 'medium', 'high'] };
  };
}

export interface SearchMatch {
  type: 'object';
  required: ['file', 'line', 'snippet'];
  properties: {
    file: FilePath;
    line: { type: 'integer'; minimum: 1 };
    snippet: { type: 'string' };
  };
}

export interface Todo {
  type: 'object';
  required: ['ref', 'description'];
  properties: {
    ref: { type: 'string' };
    description: { type: 'string' };
    suggestedAction: { type: 'string' };
  };
}

export interface ReleaseNotes {
  type: 'object';
  required: ['features', 'fixes', 'breaking'];
  properties: {
    features: { type: 'array'; items: { type: 'string' } };
    fixes: { type: 'array'; items: { type: 'string' } };
    breaking: { type: 'array'; items: { type: 'string' } };
  };
}

export interface TestFailure {
  type: 'object';
  required: ['name', 'filePath', 'message'];
  properties: {
    name: { type: 'string' };
    filePath: FilePath;
    message: { type: 'string' };
  };
}

export interface Vulnerability {
  type: 'object';
  required: ['id', 'package', 'version', 'severity'];
  properties: {
    id: { type: 'string' };
    package: { type: 'string' };
    version: { type: 'string' };
    severity: { type: 'string'; enum: ['low', 'medium', 'high', 'critical'] };
    fixedIn: { type: 'string' };
  };
}

export interface LicenseIssue {
  type: 'object';
  required: ['package', 'license', 'issue'];
  properties: {
    package: { type: 'string' };
    license: { type: 'string' };
    issue: { type: 'string' };
  };
}

// Tool Input/Output Interfaces

// refactorFunction
export interface RefactorFunctionInput {
  filePath: string;
  functionName: string;
  refactorType: 'rename' | 'extract' | 'inline' | 'introduceParam';
  newName?: string;
  range?: Range;
  preview?: boolean;
}

export interface RefactorFunctionOutput {
  patch: string;
  affectedFiles: string[];
}

// applyCodeAction
export interface ApplyCodeActionInput {
  filePath: string;
  codeActionId: string;
  preview?: boolean;
}

export interface ApplyCodeActionOutput {
  patch: string;
}

// optimizeImports
export interface OptimizeImportsInput {
  projectRoot: string;
  mode: 'file' | 'module' | 'project';
  targets?: string[] | string[];
  preview?: boolean;
}

export interface OptimizeImportsOutput {
  patches: string[];
}

// formatCode
export interface FormatCodeInput {
  targets: string[] | string[];
  style: 'ktlint' | 'spotless';
  preview?: boolean;
}

export interface FormatCodeOutput {
  patches: string[];
  summary: string;
}

// analyzeCodeQuality
export interface AnalyzeCodeQualityInput {
  scope: 'file' | 'module' | 'project';
  targets?: string[] | string[];
  ruleset: 'security' | 'performance' | 'complexity' | 'all';
  maxFindings?: number;
}

export interface AnalyzeCodeQualityOutput {
  diagnostics: Diagnostic[];
}

// generateTests
export interface GenerateTestsInput {
  filePath: string;
  classOrFunction: string;
  framework: 'JUnit5' | 'MockK';
  coverageGoal?: number;
}

export interface GenerateTestsOutput {
  files: File[];
  instructions: string;
}

// applyPatch
export interface ApplyPatchInput {
  patch: string;
  allowCreate?: boolean;
}

export interface ApplyPatchOutput {
  applied: boolean;
  conflicts?: Conflict[];
}

// androidGenerateComposeUI
export interface AndroidGenerateComposeUIInput {
  screenName: string;
  stateModel: any;
  navigation?: boolean;
  theme?: string;
}

export interface AndroidGenerateComposeUIOutput {
  files: File[];
  instructions: string;
}

// androidSetupArchitecture
export interface AndroidSetupArchitectureInput {
  pattern: 'MVVM' | 'Clean';
  di: 'Hilt' | 'Koin';
  modules?: string[];
}

export interface AndroidSetupArchitectureOutput {
  files: File[];
  gradleUpdates: GradleUpdates;
  wiringInstructions: string;
}

// androidSetupDataLayer
export interface AndroidSetupDataLayerInput {
  db: 'Room';
  entities: any[];
  migrations?: boolean;
  encryption?: boolean;
}

export interface AndroidSetupDataLayerOutput {
  files: File[];
  migrationScripts: File[];
  tests: File[];
}

// androidSetupNetwork
export interface AndroidSetupNetworkInput {
  style: 'Retrofit' | 'GraphQL' | 'WebSocket';
  endpoints: Endpoint[];
  auth: 'None' | 'ApiKey' | 'OAuth2' | 'JWT';
}

export interface AndroidSetupNetworkOutput {
  files: File[];
  tests: File[];
}

// securityEncryptData
export interface SecurityEncryptDataInput {
  dataRef: DataRef;
  algo?: 'AES-256-GCM';
  kdf?: 'PBKDF2';
  context?: any;
}

export interface SecurityEncryptDataOutput {
  encryptedRef: DataRef;
  auditId: string;
}

// securityDecryptData
export interface SecurityDecryptDataInput {
  dataRef: DataRef;
  context?: any;
}

export interface SecurityDecryptDataOutput {
  plaintextRef: DataRef;
  auditId: string;
}

// privacyRequestErasure
export interface PrivacyRequestErasureInput {
  subjectId: string;
  scopes: string[];
}

export interface PrivacyRequestErasureOutput {
  actions: string[];
  auditId: string;
}

// privacyExportData
export interface PrivacyExportDataInput {
  subjectId: string;
  format: 'JSON' | 'CSV' | 'Parquet';
  fields?: string[];
}

export interface PrivacyExportDataOutput {
  exportRef: DataRef;
  auditId: string;
}

// securityAuditTrail
export interface SecurityAuditTrailInput {
  filters?: AuditFilters;
  limit?: number;
}

export interface SecurityAuditTrailOutput {
  events: AuditEvent[];
}

// fileBackup
export interface FileBackupInput {
  targets: string[] | string[];
  dest: string;
  encrypt?: boolean;
  tag?: string;
}

export interface FileBackupOutput {
  manifest: BackupManifest;
  auditId: string;
}

// fileRestore
export interface FileRestoreInput {
  manifestRef: DataRef;
  destRoot: string;
  decrypt?: boolean;
}

export interface FileRestoreOutput {
  restored: string[];
  auditId: string;
}

// fileSyncWatch
export interface FileSyncWatchInput {
  paths: string[];
  dest: string;
  includeGlobs?: string[];
  excludeGlobs?: string[];
}

export interface FileSyncWatchOutput {
  watchId: string;
  statusStream: string;
}

// fileClassifySensitivity
export interface FileClassifySensitivityInput {
  targets: string[] | string[];
  policies: ('PII' | 'PHI' | 'Secrets')[];
}

export interface FileClassifySensitivityOutput {
  findings: ClassificationFinding[];
  recommendations: string[];
}

// gitStatus
export interface GitStatusInput {
  repoRoot: string;
}

export interface GitStatusOutput {
  branch: string;
  changes: GitChange[];
  aheadBehind: AheadBehind;
}

// gitSmartCommit
export interface GitSmartCommitInput {
  repoRoot: string;
  intent: 'refactor' | 'fix' | 'feat' | 'chore' | 'docs';
  messageHint?: string;
  include?: string[] | string[];
}

export interface GitSmartCommitOutput {
  commitId: string;
  summary: string;
}

// gitCreateFeatureBranch
export interface GitCreateFeatureBranchInput {
  repoRoot: string;
  name: string;
  from?: string;
}

export interface GitCreateFeatureBranchOutput {
  branch: string;
  tip: string;
}

// gitMergeWithResolution
export interface GitMergeWithResolutionInput {
  repoRoot: string;
  source: string;
  target: string;
  strategy?: 'recursive' | 'ours' | 'theirs' | 'ort';
}

export interface GitMergeWithResolutionOutput {
  merged: boolean;
  conflicts?: Conflict[];
  instructions?: string;
}

// apiCallSecure
export interface ApiCallSecureInput {
  spec: ApiSpec;
  body?: any;
  schema?: any;
  rateLimitKey?: string;
}

export interface ApiCallSecureOutput {
  response: any;
  latencyMs: number;
  costEst?: number;
}

// apiMonitorMetrics
export interface ApiMonitorMetricsInput {
  serviceId: string;
  window: string;
  dimensions?: string[];
}

export interface ApiMonitorMetricsOutput {
  metrics: MetricPoint[];
  alerts?: string[];
}

// apiValidateCompliance
export interface ApiValidateComplianceInput {
  payloadRef: DataRef;
  policies: ('GDPR' | 'HIPAA')[];
}

export interface ApiValidateComplianceOutput {
  violations: ComplianceViolation[];
  suggestedRemediations: string[];
}

// projectSearch
export interface ProjectSearchInput {
  query: string;
  paths?: string[] | string[];
  regex?: boolean;
  contextLines?: number;
}

export interface ProjectSearchOutput {
  matches: SearchMatch[];
}

// todoListFromCode
export interface TodoListFromCodeInput {
  scope: 'file' | 'module' | 'project';
  targets?: string[] | string[];
}

export interface TodoListFromCodeOutput {
  todos: Todo[];
}

// readmeGenerateOrUpdate
export interface ReadmeGenerateOrUpdateInput {
  projectRoot: string;
  sections?: string[];
}

export interface ReadmeGenerateOrUpdateOutput {
  file: File;
  patch: string;
}

// changelogSummarize
export interface ChangelogSummarizeInput {
  repoRoot: string;
  sinceTag: string;
  until?: string;
}

export interface ChangelogSummarizeOutput {
  notes: ReleaseNotes;
  nextVersionHint: string;
}

// buildAndTest
export interface BuildAndTestInput {
  command: 'gradle' | 'maven';
  targets?: string[];
  profile?: string;
}

export interface BuildAndTestOutput {
  status: 'passed' | 'failed';
  summary: string;
  failingTests?: TestFailure[];
  artifacts?: File[];
}

// dependencyAudit
export interface DependencyAuditInput {
  projectRoot: string;
  includeLicenses?: boolean;
  allowList?: string[];
}

export interface DependencyAuditOutput {
  vulns: Vulnerability[];
  licenseIssues?: LicenseIssue[];
  upgradeAdvice: string[];
}

// Tool Schemas Map
export interface ToolSchemas {
  [toolName: string]: {
    input: JSONSchema7;
    output: JSONSchema7;
  };
}

// Export all tool schemas
export const toolSchemas: ToolSchemas = {
  refactorFunction: {
    input: {
      type: 'object',
      required: ['filePath', 'functionName', 'refactorType'],
      properties: {
        filePath: { type: 'string', minLength: 1 },
        functionName: { type: 'string', minLength: 1 },
        refactorType: { type: 'string', enum: ['rename', 'extract', 'inline', 'introduceParam'] },
        newName: { type: 'string' },
        range: { $ref: '#/definitions/range' },
        preview: { type: 'boolean', default: false }
      }
    },
    output: {
      type: 'object',
      required: ['patch', 'affectedFiles'],
      properties: {
        patch: { type: 'string', minLength: 1 },
        affectedFiles: { type: 'array', items: { type: 'string', minLength: 1 } }
      }
    }
  },
  // Add other tool schemas here...
};
