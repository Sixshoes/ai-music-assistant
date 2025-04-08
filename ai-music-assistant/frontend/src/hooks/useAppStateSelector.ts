import { isEqual } from 'lodash-es'; // 需要安裝 lodash-es 依賴
import { useCallback, useEffect, useMemo, useRef } from 'react';
import { AppState, useAppState } from '../context/AppStateContext';

/**
 * 選擇器函數類型，從全局狀態中選擇特定部分
 */
type Selector<T> = (state: AppState) => T;

/**
 * 類似於 Redux 的 useSelector 自定義 Hook
 * 
 * @param selector 從全局狀態中選擇所需的數據的函數
 * @param equalityFn 可選的比較函數，用於決定是否應該觸發重新渲染
 * @returns 選擇的狀態
 */
export function useAppStateSelector<T>(
  selector: Selector<T>,
  equalityFn: (a: T, b: T) => boolean = isEqual
): T {
  const { state } = useAppState();
  const lastSelectedState = useRef<T>(selector(state));
  
  // 使用 useMemo 優化選擇的部分狀態，確保只有在選擇的部分發生變化時才重新計算
  const selectedState = useMemo(() => selector(state), [state, selector]);
  
  // 如果使用者提供了自定義的相等性檢查函數，則使用它
  // 否則，使用 lodash 的 isEqual 進行深度比較
  const stateChanged = !equalityFn(lastSelectedState.current, selectedState);
  
  // 僅在選擇的狀態確實發生變化時更新引用
  useEffect(() => {
    if (stateChanged) {
      lastSelectedState.current = selectedState;
    }
  }, [selectedState, stateChanged]);
  
  // 如果狀態發生變化，返回新狀態；否則返回上一個引用的狀態
  return stateChanged ? selectedState : lastSelectedState.current;
}

/**
 * 僅針對特定狀態部分的 action 創建器，優化渲染效率
 * 
 * @param actionCreator 創建 action 的函數
 * @returns 綁定到 dispatch 的 action 創建器
 */
export function useActionCreator<T extends Array<any>, R>(
  actionCreator: (...args: T) => R
) {
  const { dispatch } = useAppState();
  
  return useCallback(
    (...args: T) => {
      const action = actionCreator(...args);
      dispatch(action as any);
    },
    [actionCreator, dispatch]
  );
}

/**
 * 創建綁定到 dispatch 的 action 創建器
 * @param type action 類型
 * @returns 綁定到 dispatch 的函數
 */
export function useAction<T>(type: string) {
  const { dispatch } = useAppState();
  
  return useCallback(
    (payload: T) => {
      dispatch({ type, payload } as any);
    },
    [dispatch, type]
  );
} 