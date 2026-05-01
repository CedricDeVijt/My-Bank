export interface User {
  user_id: string;
  email: string;
  status: string;
}

export interface UserCreate {
  email: string;
  password: string;
  fist_name: string;
  last_name: string;
  date_of_birth: Date;
}

export interface UserLogin {
  email: string;
  password: string;
}
