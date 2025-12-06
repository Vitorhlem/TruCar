import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Maintenance } from './maintenance';

describe('Maintenance', () => {
  let component: Maintenance;
  let fixture: ComponentFixture<Maintenance>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Maintenance]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Maintenance);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
