import { Component, Input, OnInit } from '@angular/core';
import { SharedService } from '../services/shared/shared.service';

@Component({
  selector: 'app-loading',
  templateUrl: './loading.component.html',
  styleUrls: ['./loading.component.css']
})
export class LoadingComponent implements OnInit{
  isLoading: boolean = false;
  constructor(private sharedService:SharedService){

  }
  
  ngOnInit(): void {
    this.sharedService.currentLoading.subscribe(result => {
      this.isLoading = result;
    });
  }
}
