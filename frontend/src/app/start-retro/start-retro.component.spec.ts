import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { StartRetroComponent } from './start-retro.component';

describe('StartRetroComponent', () => {
  let component: StartRetroComponent;
  let fixture: ComponentFixture<StartRetroComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ StartRetroComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(StartRetroComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
