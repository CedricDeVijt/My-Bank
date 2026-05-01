export interface Account {
  account_id: string;
  account_number: string;
  iban: string;
  type: string;
  currency: string;
  balance_cents: number;
  status: string;
  created_at: Date;
}

export interface AccountCreate {
  type: string;
  currency: string;
}
