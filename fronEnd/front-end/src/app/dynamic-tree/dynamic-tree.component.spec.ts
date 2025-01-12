import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DynamicTreeComponent } from './dynamic-tree.component';

describe('DynamicTreeComponent', () => {
  let component: DynamicTreeComponent;
  let fixture: ComponentFixture<DynamicTreeComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [DynamicTreeComponent]
    });
    fixture = TestBed.createComponent(DynamicTreeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
