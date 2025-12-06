import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LiveMap } from './live-map';

describe('LiveMap', () => {
  let component: LiveMap;
  let fixture: ComponentFixture<LiveMap>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LiveMap]
    })
    .compileComponents();

    fixture = TestBed.createComponent(LiveMap);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
