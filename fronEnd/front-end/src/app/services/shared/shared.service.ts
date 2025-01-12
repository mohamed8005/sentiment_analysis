// src/app/services/shared.service.ts
import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SharedService {
  private resultSource = new BehaviorSubject<string>(''); // Initialisé avec une chaîne vide
  private resultSource2 = new BehaviorSubject<any>(''); // Initialisé avec une chaîne vide
  private loading = new BehaviorSubject<boolean>(false); // Initialisé avec une chaîne vide
  currentResult = this.resultSource.asObservable();
  currentResultComp = this.resultSource2.asObservable();
  currentLoading = this.loading.asObservable();
  constructor() { }

  updateResult(result: string) {
    this.resultSource.next(result);
  }
  updateResult2(result: any) {
    this.resultSource2.next(result);
  }
  loadingPage(result: boolean) {
    this.loading.next(result);
  }
}
