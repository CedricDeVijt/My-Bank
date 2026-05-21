export interface Token {
  token_type: string;
  access_token: string;
  refresh_token: string;
  access_token_expires_in: number;
  refresh_token_expires_in: number;
  saved_at?: number;
}

export type TokenResponse = Token;
