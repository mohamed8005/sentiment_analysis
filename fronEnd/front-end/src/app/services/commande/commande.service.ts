import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class CommandeService {

  private backendUrl = 'http://localhost:5000/command'; 
  private backendUrl2 = 'http://localhost:5000/export'; 

  constructor(private http: HttpClient) { }

  envoyerCommande(commande: any): Observable<any> {
    return this.http.post(this.backendUrl, commande);
  }
  export(commande: any): Observable<any> {
    return this.http.post(this.backendUrl2, commande,{
      responseType: 'blob'
    });
  }
}
