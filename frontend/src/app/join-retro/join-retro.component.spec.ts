import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { JoinRetroComponent } from './join-retro.component';

describe('JoinRetroComponent', () => {
  let component: JoinRetroComponent;
  let fixture: ComponentFixture<JoinRetroComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ JoinRetroComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(JoinRetroComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
