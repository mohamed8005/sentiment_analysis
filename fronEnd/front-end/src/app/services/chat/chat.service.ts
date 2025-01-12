import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { HttpClient } from '@angular/common/http';
@Injectable({
  providedIn: 'root'
})
export class ChatService {

  private backendUrl = 'http://localhost:5000/chat';

  constructor(private http: HttpClient) { }

  envoyerMessage(message: any): Observable<any> {
    // Simuler une réponse du backend
    const reponse = `Réponse à: "${message}"`;
    return this.http.post(this.backendUrl, message);
    // return of(reponse);
  }
}
