export interface User {
  user_id: string;
  email: string;
  status: string;
}

export interface UserCreate {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface UserResponse {
  first_name: string;
  last_name: string;
  email: string;
}
