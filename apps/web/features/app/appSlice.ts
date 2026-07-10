import { createSlice } from '@reduxjs/toolkit';

interface AppState {
  ready: boolean;
}

const initialState: AppState = {
  ready: true,
};

const appSlice = createSlice({
  name: 'app',
  initialState,
  reducers: {},
});

export const appReducer = appSlice.reducer;
