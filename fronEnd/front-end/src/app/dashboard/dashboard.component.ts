// src/app/dashboard/dashboard.component.ts
import { Component, OnInit ,Renderer2} from '@angular/core';
import { SharedService } from '../services/shared/shared.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {

  result: string = '';
  result2: any ='';

  machineLearning = false;
  visible = false;

  constructor(private sharedService: SharedService,private renderer: Renderer2) { }

  ngOnInit(): void {
    this.sharedService.currentResult.subscribe(result => {
      this.result = result;
    });
    this.sharedService.currentResultComp.subscribe(result => {
      this.result2 = result;
    });
  }

  toggleAI(): void {
    this.machineLearning = !this.machineLearning;
    if (this.machineLearning) {
      this.renderer.setStyle(document.body, 'background-color', '#e0f7fa');
    } else {
      this.renderer.removeStyle(document.body, 'background-color');
    }
  }
  toggleVisible(): void {
    this.visible = !this.visible;
  }

}
