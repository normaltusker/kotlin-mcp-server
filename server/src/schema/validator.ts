/**
 * MCP Tool Validators - TypeScript Implementation
 *
 * Uses Ajv v8 (2020-12) with ajv-formats for schema validation.
 */

import Ajv from 'ajv';
import addFormats from 'ajv-formats';
import { toolSchemas } from './types';

// Initialize Ajv with 2020-12 draft support
const ajv = new Ajv({
  strict: true,
  allErrors: true,
  useDefaults: true,
  coerceTypes: false,
  removeAdditional: false,
  validateFormats: true,
  $data: true,
});

// Add format support
addFormats(ajv);

// Compile validators for each tool
const inputValidators: { [toolName: string]: Ajv.ValidateFunction } = {};
const outputValidators: { [toolName: string]: Ajv.ValidateFunction } = {};

for (const [toolName, schemas] of Object.entries(toolSchemas)) {
  try {
    inputValidators[toolName] = ajv.compile(schemas.input);
    outputValidators[toolName] = ajv.compile(schemas.output);
  } catch (error) {
    console.error(`Failed to compile validator for ${toolName}:`, error);
  }
}

// Custom error classes
export class ValidationError extends Error {
  constructor(
    public code: string,
    public message: string,
    public data?: any
  ) {
    super(message);
    this.name = 'ValidationError';
  }
}

export class SchemaMissingError extends Error {
  constructor(toolName: string) {
    super(`Schema not found for tool: ${toolName}`);
    this.name = 'SchemaMissingError';
  }
}

// Validation functions
export function validateInput(toolName: string, data: any): void {
  const validator = inputValidators[toolName];
  if (!validator) {
    throw new SchemaMissingError(toolName);
  }

  const valid = validator(data);
  if (!valid) {
    throw new ValidationError(
      'ValidationError',
      `Input validation failed for ${toolName}`,
      { errors: validator.errors }
    );
  }
}

export function validateOutput(toolName: string, data: any): void {
  const validator = outputValidators[toolName];
  if (!validator) {
    throw new SchemaMissingError(toolName);
  }

  const valid = validator(data);
  if (!valid) {
    throw new ValidationError(
      'InternalOutputInvalid',
      `Output validation failed for ${toolName}`,
      { errors: validator.errors }
    );
  }
}

// Utility function to get available tools
export function getAvailableTools(): string[] {
  return Object.keys(toolSchemas);
}

// Utility function to get tool schema
export function getToolSchema(toolName: string) {
  return toolSchemas[toolName];
}
