import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ViewRetroComponent } from './view-retro.component';

describe('ViewRetroComponent', () => {
  let component: ViewRetroComponent;
  let fixture: ComponentFixture<ViewRetroComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ViewRetroComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ViewRetroComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
