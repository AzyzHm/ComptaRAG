import { HttpInterceptorFn } from '@angular/common/http';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const token = localStorage.getItem('access_token');

  if (!token) {
    return next(req);
  }

  const authedRequest = req.clone({
    setHeaders: { Authorization: `Bearer ${token}` }
  });

  return next(authedRequest);
};
